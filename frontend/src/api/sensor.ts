import type { AggregatedSensorData, ProcessedSensorData, RawSensorData, TimestampRange } from '@/types'
import axios from './axios'

export default function SensorAPI() {
    const create = async (sensor: RawSensorData) => {
        try {
            const response = await axios.post<RawSensorData>('/sensor/data/', sensor)
            return response.data
        } catch (error) {
            console.error('Error creating sensor:', error)
            throw error
        }
    }

    const getProcessed = async (range: TimestampRange) => {
        try {
            const response = await axios.get<ProcessedSensorData[]>('/sensor/processed/', { params: range })
            return response.data
        } catch (error) {
            console.error('Error fetching processed sensor data:', error)
            throw error
        }
    }

    const getAggregated = async (range: TimestampRange) => {
        try {
            const response = await axios.get<AggregatedSensorData>('/sensor/aggregated/', { params: range })
            return response.data
        } catch (error) {
            console.error('Error fetching aggregated sensor data:', error)
            throw error
        }
    }

    return {
        create,
        getProcessed,
        getAggregated,
    }
}