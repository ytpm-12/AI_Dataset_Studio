const API_ROOT = '/api/v1'

let csrfToken = null

function extractMessage(payload, fallback) {
  if (!payload) return fallback
  if (typeof payload === 'string') return payload
  if (payload.detail) return payload.detail

  const firstEntry = Object.entries(payload)[0]
  if (!firstEntry) return fallback
  const [field, value] = firstEntry
  const message = Array.isArray(value) ? value[0] : value
  return field === 'non_field_errors' ? String(message) : `${field}: ${message}`
}

async function parseResponse(response) {
  if (response.status === 204) return null
  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) return response.json()
  return response.text()
}

export async function ensureCsrf() {
  if (csrfToken) return csrfToken
  const response = await fetch(`${API_ROOT}/auth/csrf/`, { credentials: 'include' })
  const payload = await parseResponse(response)
  if (!response.ok) throw new Error(extractMessage(payload, 'Impossible d’obtenir le jeton CSRF.'))
  csrfToken = payload.csrfToken
  return csrfToken
}

export async function apiRequest(path, options = {}) {
  const method = options.method || 'GET'
  const headers = new Headers(options.headers || {})
  const unsafe = !['GET', 'HEAD', 'OPTIONS'].includes(method.toUpperCase())

  if (unsafe) headers.set('X-CSRFToken', await ensureCsrf())
  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(`${API_ROOT}${path}`, {
    ...options,
    method,
    headers,
    credentials: 'include',
  })
  const payload = await parseResponse(response)

  if (!response.ok) {
    const error = new Error(extractMessage(payload, `Erreur HTTP ${response.status}`))
    error.status = response.status
    error.payload = payload
    throw error
  }

  return payload
}

export const api = {
  currentUser: () => apiRequest('/auth/me/'),
  login: (credentials) => apiRequest('/auth/login/', { method: 'POST', body: JSON.stringify(credentials) }),
  register: (values) => apiRequest('/auth/register/', { method: 'POST', body: JSON.stringify(values) }),
  logout: () => apiRequest('/auth/logout/', { method: 'POST' }),
  projects: () => apiRequest('/projects/'),
  createProject: (values) => apiRequest('/projects/', { method: 'POST', body: JSON.stringify(values) }),
  uploads: () => apiRequest('/uploads/'),
  upload: (formData) => apiRequest('/uploads/', { method: 'POST', body: formData }),
  uploadDetail: (id) => apiRequest(`/uploads/${id}/`),
  uploadPreview: (id, limit = 20) => apiRequest(`/uploads/${id}/preview/?limit=${limit}`),
  jobs: (query = '') => apiRequest(`/jobs/${query}`),
  retryJob: (id) => apiRequest(`/jobs/${id}/retry/`, { method: 'POST' }),
}
