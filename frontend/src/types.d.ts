export type Choice = "temperature" | "humidity" | "air_quality"
export type RawSensorData = {
    id?: number;
    timestamp?: string;
    temperature: number | null;
    humidity: number | null;
    air_quality: number | null;
}

export type TimestampRange = {
    timestamp_after: string | null;
    timestamp_before: string | null;
};


// {
//     "timestamp": "2025-01-29T11:48:03Z",
//     "temperature": {
//         "value": 24.05,
//         "z_score": -0.5508185800978972,
//         "anomaly": false
//     },
//     "humidity": {
//         "value": 63.61,
//         "z_score": 0.5540782924643602,
//         "anomaly": false
//     },
//     "air_quality": {
//         "value": 66.48,
//         "z_score": -1.1355762540951313,
//         "anomaly": false
//     }
// },

export type ProcessedData = {
    value: number;
    z_score: number;
    anomaly: boolean;
}
export type ProcessedSensorData = {
    timestamp: string;
    temperature: ProcessedData;
    humidity: ProcessedData;
    air_quality: ProcessedData;
    [key: Choice]: ProcessedData;
}

export type Aggregated = {
    mean: number | null;
    median: number | null;
    sd: number | null;
    min: number | null;
    max: number | null;
}
export type AggregatedSensorData = {
    temperature: Aggregated;
    humidity: Aggregated;
    air_quality: Aggregated;
    [key: Choice]: Aggregated;
}

