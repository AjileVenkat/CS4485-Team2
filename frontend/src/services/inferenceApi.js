import { API_URL } from '../constants/modelConfig'

const inferHealthEndpoint = (endpoint) => {
  try {
    const parsed = new URL(endpoint)
    parsed.pathname = '/health'
    parsed.search = ''
    return parsed.toString()
  } catch {
    return null
  }
}

export const requestServiceHealth = async (endpoint = API_URL) => {
  const healthEndpoint = inferHealthEndpoint(endpoint)
  if (!healthEndpoint) {
    throw new Error('Service URL is invalid.')
  }

  const response = await fetch(healthEndpoint, {
    method: 'GET',
  })

  if (!response.ok) {
    throw new Error(`Service health check failed (${response.status})`)
  }

  return response.json()
}

export const requestLiveInference = async (file, endpoint = API_URL) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(endpoint, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    let detail = ''

    try {
      const body = await response.json()
      detail = body?.detail ? `: ${body.detail}` : ''
    } catch {
      detail = ''
    }

    throw new Error(`Service request failed (${response.status})${detail}`)
  }

  return response.json()
}
