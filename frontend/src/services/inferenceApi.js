import { API_URL } from '../constants/modelConfig'

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

    throw new Error(`Backend request failed (${response.status})${detail}`)
  }

  return response.json()
}
