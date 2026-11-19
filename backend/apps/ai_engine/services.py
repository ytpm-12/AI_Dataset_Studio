import json
import urllib.error
import urllib.request

from django.conf import settings

from apps.pipelines.services import build_quality_report

from .models import AIRecommendation


ALLOWED_ACTIONS = {
    'impute_missing', 'drop_duplicates', 'review_duplicates', 'cast_type',
    'standardize_format', 'normalize_text', 'review_outliers', 'scale_numeric',
    'encode_categorical', 'flag_class_imbalance', 'validate_integrity',
    'request_human_review', 'no_action', 'reject_unsupported',
}

RECOMMENDATION_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'required': [
        'action', 'target', 'parameters', 'confidence', 'explanation',
        'requires_validation',
    ],
    'properties': {
        'action': {'type': 'string', 'enum': sorted(ALLOWED_ACTIONS)},
        'target': {'type': 'string'},
        'parameters': {'type': 'object'},
        'confidence': {'type': 'number', 'minimum': 0, 'maximum': 1},
        'explanation': {'type': 'string'},
        'requires_validation': {'type': 'boolean'},
    },
}


class AIServiceUnavailable(RuntimeError):
    pass


class InvalidAIResponse(ValueError):
    pass


def validate_recommendation(payload):
    if not isinstance(payload, dict):
        raise InvalidAIResponse("La réponse IA n'est pas un objet JSON.")
    required = set(RECOMMENDATION_SCHEMA['required'])
    if set(payload) != required:
        raise InvalidAIResponse('La réponse IA ne respecte pas les champs du contrat.')
    if payload['action'] not in ALLOWED_ACTIONS:
        raise InvalidAIResponse("L'action recommandée est inconnue.")
    if not isinstance(payload['target'], str) or not payload['target'].strip():
        raise InvalidAIResponse('La cible recommandée est invalide.')
    if not isinstance(payload['parameters'], dict):
        raise InvalidAIResponse('Les paramètres doivent être un objet JSON.')
    confidence = payload['confidence']
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise InvalidAIResponse('La confiance doit être comprise entre 0 et 1.')
    if not isinstance(payload['explanation'], str) or not payload['explanation'].strip():
        raise InvalidAIResponse("L'explication est obligatoire.")
    if not isinstance(payload['requires_validation'], bool):
        raise InvalidAIResponse('requires_validation doit être booléen.')
    if payload['action'] not in {'no_action', 'reject_unsupported'} and not payload['requires_validation']:
        raise InvalidAIResponse('Toute action de transformation exige une validation humaine.')
    return payload


def deterministic_recommendation(profile, quality):
    columns = profile.get('columns', [])
    for column in columns:
        missing_count = int(column.get('missing_count') or 0)
        if missing_count:
            ratio = (missing_count / quality['analyzed_rows']) if quality['analyzed_rows'] else 0
            if ratio > 0.5:
                return {
                    'action': 'request_human_review', 'target': column['name'],
                    'parameters': {}, 'confidence': 0.99,
                    'explanation': 'Plus de la moitié des valeurs de cette colonne sont absentes.',
                    'requires_validation': True,
                }
            strategy = 'median' if any(token in column.get('dtype', '') for token in ('int', 'float')) else 'mode'
            return {
                'action': 'impute_missing', 'target': column['name'],
                'parameters': {'strategy': strategy}, 'confidence': 0.98,
                'explanation': 'Des valeurs manquantes ont été détectées dans cette colonne.',
                'requires_validation': True,
            }
    if quality['duplicate_rows'] > 0:
        return {
            'action': 'drop_duplicates', 'target': 'dataset',
            'parameters': {'keep': 'first'}, 'confidence': 0.99,
            'explanation': 'Des lignes strictement identiques ont été détectées.',
            'requires_validation': True,
        }
    return None


def _system_prompt():
    return (
        'Tu es le moteur de recommandation qualité de AI Dataset Studio. '
        'Analyse uniquement le profil statistique fourni. Ne modifie jamais les données. '
        'Choisis une seule action autorisée. Si le profil est ambigu, choisis '
        'request_human_review. Toute transformation exige requires_validation=true. '
        'Réponds uniquement avec un objet JSON conforme au schéma imposé, sans markdown.'
    )


def _post_json(url, payload, headers=None):
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False, default=str).encode('utf-8'),
        headers={'Content-Type': 'application/json', **(headers or {})},
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=settings.AI_REQUEST_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode('utf-8'))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise AIServiceUnavailable("Le service d'IA est indisponible ou a répondu incorrectement.") from exc


def request_model_recommendation(profile_snapshot):
    messages = [
        {'role': 'system', 'content': _system_prompt()},
        {'role': 'user', 'content': json.dumps(profile_snapshot, ensure_ascii=False, default=str)},
    ]
    if settings.AI_PROVIDER == 'ollama':
        response = _post_json(
            f"{settings.AI_BASE_URL.rstrip('/')}/api/chat",
            {
                'model': settings.AI_MODEL_NAME,
                'messages': messages,
                'stream': False,
                'think': False,
                'format': RECOMMENDATION_SCHEMA,
                'options': {'temperature': 0, 'num_ctx': 2048, 'num_predict': 256},
            },
        )
        raw_content = response.get('message', {}).get('content', '')
        engine = AIRecommendation.Engine.OLLAMA
    else:
        headers = {'Authorization': f'Bearer {settings.AI_API_KEY}'} if settings.AI_API_KEY else {}
        response = _post_json(
            f"{settings.AI_BASE_URL.rstrip('/')}/v1/chat/completions",
            {
                'model': settings.AI_MODEL_NAME,
                'messages': messages,
                'temperature': 0,
                'response_format': {'type': 'json_schema', 'json_schema': {'name': 'dataset_recommendation', 'schema': RECOMMENDATION_SCHEMA}},
            },
            headers,
        )
        raw_content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        engine = AIRecommendation.Engine.OPENAI_COMPATIBLE
    try:
        recommendation = json.loads(raw_content)
    except (TypeError, json.JSONDecodeError) as exc:
        raise InvalidAIResponse("Le modèle n'a pas retourné un JSON valide.") from exc
    return validate_recommendation(recommendation), engine


def generate_recommendation(uploaded_file, force_ai=False):
    quality = build_quality_report(uploaded_file, settings.CLEANING_ANALYSIS_MAX_ROWS)
    quality['generated_at'] = quality['generated_at'].isoformat()
    profile_snapshot = {'profile': uploaded_file.profile, 'quality': quality}
    recommendation = None if force_ai else deterministic_recommendation(uploaded_file.profile, quality)
    if recommendation:
        engine = AIRecommendation.Engine.RULES
        model_name = ''
    else:
        recommendation, engine = request_model_recommendation(profile_snapshot)
        model_name = settings.AI_MODEL_NAME
    return AIRecommendation.objects.create(
        owner=uploaded_file.owner,
        uploaded_file=uploaded_file,
        engine=engine,
        model_name=model_name,
        profile_snapshot=profile_snapshot,
        recommendation=recommendation,
    )
