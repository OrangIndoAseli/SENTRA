import { defineStore } from 'pinia'
import api from '../services/api'

export const useSentraStore = defineStore('sentra', {
  state: () => ({
    stats: {}, alerts: [], violations: [], cameras: [], zones: [],
    detectionResult: null, health: null, loading: false, error: null
  }),
  actions: {
    async fetchDashboard() {
      const { data } = await api.get('/dashboard')
      const payload = data.data || {}
      this.stats = payload.stats || {}
      this.alerts = payload.alerts || []
      this.violations = payload.violations || []
      this.cameras = payload.cameras || []
    },
    async fetchViolations() {
      const { data } = await api.get('/detections')
      this.violations = data.data || []
    },
    async fetchZones() {
      const { data } = await api.get('/danger-zones')
      this.zones = data.data || []
    },
    async addCamera(camera) {
      const { data } = await api.post('/cameras', camera)
      this.cameras.push(data.data)
      return data.data
    },
    async addZone(zone) {
      const { data } = await api.post('/danger-zones', zone)
      this.zones.push(data.data)
      return data.data
    },
    async checkHealth() {
      const { data } = await api.get('/health')
      this.health = data
    },
    async detectImage(file, cameraCode = 'CAM-01', { persist = true } = {}) {
      this.loading = true
      this.error = null
      const form = new FormData()
      form.append('image', file)
      form.append('camera_code', cameraCode)
      form.append('persist', persist ? '1' : '0')
      try {
        const { data } = await api.post('/detect-image', form)
        this.detectionResult = data.data.result
        if (persist) await this.fetchDashboard()
        return data
      } catch (error) {
        this.error = error.response?.data?.message || error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async reportLiveViolation(payload) {
      const { data } = await api.post('/detections', payload)
      await this.fetchDashboard()
      return data
    },
    async resolveAlert(id) {
      await api.put(`/alerts/${id}`, { status: 'resolved' })
      await this.fetchDashboard()
    }
  }
})
