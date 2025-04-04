<script setup lang="ts">
import SensorAPI from "@/api/sensor";
import { ref } from "vue";

const sensorAPI = SensorAPI();

const interval = ref<number>(5);
const temperature = ref<number>(25);
const humidity = ref<number>(50);
const airQuality = ref<number>(100);
const isRunning = ref<boolean>(false);
const sendCount = ref<number>(0);

let intervalId: ReturnType<typeof setInterval> | null = null;

// Function to simulate API call
const sendSensorData = async () => {
  const payload = {
    temperature: temperature.value,
    humidity: humidity.value,
    air_quality: airQuality.value,
    // timestamp: new Date().toISOString(),
  };

  try {
    await sensorAPI.create(payload)
    sendCount.value += 1;
  } catch (error) {
    console.error("Failed to send sensor data:", error);
  }
};

const startSimulation = () => {
  if (isRunning.value || interval.value < 1) return;

  isRunning.value = true;
  sendSensorData();
  intervalId = setInterval(sendSensorData, interval.value * 1000);
};

const stopSimulation = () => {
  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
  isRunning.value = false;
};
</script>

<template>
  <div class="border-1 border-gray-200 rounded p-2 px-4 flex flex-col gap-2">
    <h2 class="text-center text-xl font-bold">Sensor Simulator</h2>

    <div class="grid grid-cols-2 gap-2">
      <label>
        Interval (seconds):
        <input class="border border-gray-300 text-sm rounded block w-full p-1.5 transition-opacity disabled:opacity-20" v-model.number="interval" type="number" min="1" :disabled="isRunning" />
      </label>

      <label>
        Temperature:
        <input class="border border-gray-300 text-sm rounded block w-full p-1.5" v-model.number="temperature" type="number" />
      </label>

      <label>
        Humidity:
        <input class="border border-gray-300 text-sm rounded block w-full p-1.5" v-model.number="humidity" type="number" />
      </label>

      <label>
        Air Quality:
        <input class="border border-gray-300 text-sm rounded block w-full p-1.5" v-model.number="airQuality" type="number" />
      </label>
    </div>

    <div class="text-center">
        <span class="rounded-full bg-gray-200 px-2 py-1 text-sm">Send: {{ sendCount }}</span>
    </div>

    <div class="flex justify-center gap-2">
      <button class="bg-green-600 text-white py-1.5 px-4 text-sm rounded cursor-pointer hover:opacity-80 transition-opacity disabled:opacity-20" @click="startSimulation" :disabled="isRunning">Start</button>
      <button class="bg-red-500 text-white py-1.5 px-4 text-sm rounded cursor-pointer hover:opacity-80 transition-opacity disabled:opacity-20" @click="stopSimulation" :disabled="!isRunning">Stop</button>
    </div>
  </div>
</template>
