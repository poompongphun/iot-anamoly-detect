<script lang="ts" setup>
import SensorChart from "@/components/SensorChart.vue";
import { onMounted, ref } from "vue";
import moment from "moment";
import type { AggregatedSensorData, Choice, ProcessedSensorData, TimestampRange } from "@/types";
import SensorAPI from "@/api/sensor";

const choices = ["temperature", "humidity", "air_quality"];
const preRange = [
  { label: "All times", value: 0 },
  { label: "Last 10 minutes", value: 10 * 60 },
  { label: "Last 1 hour", value: 60 * 60 },
  { label: "Last 24 hours", value: 24 * 60 * 60 },
];

const sensorAPI = SensorAPI();

const selected = ref<Choice>(choices[0] as Choice);
const range = ref<TimestampRange>({ timestamp_after: null, timestamp_before: null });
const showCustomRange = ref(false);
const loading = ref(false);

const processedData = ref<ProcessedSensorData[]>([]);
const aggregatedData = ref<AggregatedSensorData>();

const updateRange = async (event: Event) => {
  const target = event.target as HTMLSelectElement;
  const value = target.value;

  if (value === "custom") {
    showCustomRange.value = true;
    return;
  }

  if (value === "0") {
    range.value = { timestamp_after: null, timestamp_before: null };
    await fetchData();
    return;
  }

  showCustomRange.value = false;
  const timestamp_after = moment().subtract(value, "seconds").toISOString();
  const timestamp_before = moment().toISOString();
  range.value = { timestamp_after, timestamp_before };
  await fetchData();
};

const fetchProcessedData = async () => {
  const response = await sensorAPI.getProcessed(range.value);
  return response;
};

const fetchAggregatedData = async () => {
  const response = await sensorAPI.getAggregated(range.value);
  return response;
};

const fetchData = async () => {
  loading.value = true;

  try {
    const [processed, aggregated] = await Promise.all([
      fetchProcessedData(),
      fetchAggregatedData(),
    ]);

    processedData.value = processed;
    aggregatedData.value = aggregated;
  } catch (error) {
    console.error("Error fetching data:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await fetchData();
});
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-center py-3">IoT Data Processing</h1>

    <div class="flex flex-col justify-center relative mx-4">
      <div class="flex justify-between">
        <div
          class="flex item-center border-t border-x border-gray-300 rounded-t overflow-hidden"
        >
          <button
            v-for="(item, index) in choices"
            :key="index"
            class="px-4 py-2 cursor-pointer hover:bg-gray-100 transition-colors"
            :class="{
              'bg-gray-200': item === selected,
            }"
            :disabled="item === selected"
            @click="selected = item as Choice"
          >
            {{ item }}
          </button>
        </div>

        <div>
          <select
            id="range"
            class="border border-gray-300 text-sm rounded block w-full p-1.5"
            @change="updateRange"
          >
            <option v-for="(item, index) in preRange" :key="index" :value="item.value">
              {{ item.label }}
            </option>
            <option value="custom">Custom</option>
          </select>
        </div>
      </div>

      <div class="border-1 border-gray-300 rounded-r rounded-b w-full">
        <div v-if="loading" class="text-center py-5">Loading...</div>
        <SensorChart
          v-else-if="processedData.length > 0 && aggregatedData"
          :types="selected"
          :data="processedData"
          :aggegrated-data="aggregatedData"
        />

        <div v-else class="text-center py-5">No Data</div>
      </div>
    </div>
  </div>
</template>
