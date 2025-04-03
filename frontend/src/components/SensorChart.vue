<script setup lang="ts">
import { onMounted, ref, shallowRef, watch } from "vue";
import { Chart, registerables, type ChartDataCustomTypesPerDataset } from "chart.js";
import type { AggregatedSensorData, Choice, ProcessedSensorData } from "@/types";

const { types, data, aggegratedData } = defineProps<{
  types: Choice;
  data: ProcessedSensorData[];
  aggegratedData: AggregatedSensorData;
}>();

Chart.register(...registerables);

const chartCanvas = ref<HTMLCanvasElement | null>(null);
const currentChart = shallowRef<Chart | null>(null);

const getChartData = (): any => {
  const dotData = data.map((d) => {
    return { x: new Date(d.timestamp).toLocaleString(), y: d[types].value };
  });

  const aggData = aggegratedData[types];
  const median = aggData.median || 0;
  const sd = aggData.sd || 0;
  return {
    datasets: [
      {
        type: "scatter",
        label: "Anomalies",
        data: dotData,
        backgroundColor: data.map((d) => {
          if (d[types].anomaly) {
            return 'hsl(352, 100%, 52%)';
          } else if (d['air_quality'].anomaly || d['humidity'].anomaly || d['temperature'].anomaly) {
            return "hsl(24, 100%, 50%)";
          }
          return 'hsl(352, 100%, 52%)';
        }),
        pointRadius: data.map((d) => {
          if (d[types].anomaly) {
            return 6;
          } else if (d['air_quality'].anomaly || d['humidity'].anomaly || d['temperature'].anomaly) {
            return 3;
          }
          return 0;
        }),
      },
      {
        type: "line",
        label: "Line Dataset",
        data: data.map((d) => ({
          x: new Date(d.timestamp).toLocaleString(),
          y: d[types].value,
        })),
        backgroundColor: "hsl(240, 100%, 33%)",
        borderColor: "hsl(240, 100%, 33%)",
      },

      {
        type: "line",
        label: "Mean + 3SD",
        data: [
          {
            x: dotData[0].x,
            y: median + sd * 3,
          },
          {
            x: dotData[dotData.length - 1].x,
            y: median + sd * 3,
          },
        ],
        borderColor: "hsla(243, 89%, 56%, 0.2)",
        backgroundColor: "hsla(243, 89%, 56%, 0.2)",
        fill: "+1",
      },
      {
        type: "line",
        label: "Mean + 2SD",
        data: [
          {
            x: dotData[0].x,
            y: median + sd * 2,
          },
          {
            x: dotData[dotData.length - 1].x,
            y: median + sd * 2,
          },
        ],
        borderColor: "hsla(119, 97%, 59%, 0.5)",
        backgroundColor: "hsla(119, 97%, 59%, 0.5)",
        fill: "+1",
      },
      {
        type: "line",
        label: "Mean + SD",
        data: [
          { x: dotData[0].x, y: median + sd },
          {
            x: dotData[dotData.length - 1].x,
            y: median + sd,
          },
        ],
        borderColor: "hsla(360, 100%, 58%, 0.2)",
        backgroundColor: "hsla(360, 100%, 58%, 0.2)",
        fill: "+1",
      },
      {
        type: "line",
        label: "Mean",
        data: [
          { x: dotData[0].x, y: median },
          {
            x: dotData[dotData.length - 1].x,
            y: median,
          },
        ],
        borderColor: "red"
      },
      {
        type: "line",
        label: "Mean - SD",
        data: [
          { x: dotData[0].x, y: median - sd },
          {
            x: dotData[dotData.length - 1].x,
            y: median - sd,
          },
        ],
        borderColor: "hsla(38, 99%, 50%, 0.2)",
        backgroundColor: "hsla(38, 99%, 50%, 0.2)",
        fill: "-1",
      },
      {
        type: "line",
        label: "Mean + 2SD",
        data: [
          {
            x: dotData[0].x,
            y: median - sd * 2,
          },
          {
            x: dotData[dotData.length - 1].x,
            y: median - sd * 2,
          },
        ],
        borderColor: "hsla(119, 97%, 59%, 0.2)",
        backgroundColor: "hsla(119, 97%, 59%, 0.2)",
        fill: "-1",
      },
      {
        type: "line",
        label: "Mean + 3SD",
        data: [
          {
            x: dotData[0].x,
            y: median - sd * 3,
          },
          {
            x: dotData[dotData.length - 1].x,
            y: median - sd * 3,
          },
        ],
        borderColor: "hsla(271, 94%, 56%, 0.2)",
        backgroundColor: "hsla(271, 94%, 56%, 0.2)",
        fill: "-1",
      },
    ],
  };
};

const createChart = () => {
  if (!chartCanvas.value) return;
  const ctx = chartCanvas.value.getContext("2d");
  if (!ctx) return;

  currentChart.value = new Chart(ctx, {
    data: getChartData(),
    options: {
      scales: {
        x: {
          title: { display: true, text: "Time Stamp" },
          type: 'category',
          labels: data.map(d => new Date(d.timestamp).toLocaleString()),
        },
        y: { title: { display: true, text: types } },
      },
    },
  });
};

const updateChart = () => {
  if (currentChart.value) {
    currentChart.value.data = getChartData();
    if (
      currentChart.value.options.scales?.y &&
      "title" in currentChart.value.options.scales.y
    ) {
      (currentChart.value.options.scales.y as any).title.text = types;
    }
    currentChart.value.update();
  }
};

onMounted(createChart);
watch(() => types, updateChart);
</script>

<template>
  <div>
    <div class="flex gap-2 justify-center py-2">
      <span class="rounded-full bg-gray-200 px-2 py-1 text-sm">
        mean: {{ aggegratedData[types].mean }}
      </span>

      <span class="rounded-full bg-gray-200 px-2 py-1 text-sm">
        median: {{ aggegratedData[types].median }}
      </span>

      <span class="rounded-full bg-gray-200 px-2 py-1 text-sm">
        sd: {{ aggegratedData[types].sd }}
      </span>

      <span class="rounded-full bg-gray-200 px-2 py-1 text-sm">
        min: {{ aggegratedData[types].min }}
      </span>

      <span class="rounded-full bg-gray-200 px-2 py-1 text-sm">
        max: {{ aggegratedData[types].max }}
      </span>
    </div>

    <canvas ref="chartCanvas"></canvas>
  </div>
</template>
