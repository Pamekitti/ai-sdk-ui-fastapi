"use client";

import { useEffect, useRef } from "react";
import * as echarts from "echarts";

interface ChartProps {
    options: any;
}

export function Chart({ options }: ChartProps) {
    const chartRef = useRef<HTMLDivElement>(null);
    const chartInstance = useRef<echarts.ECharts | null>(null);

    useEffect(() => {
        if (!chartRef.current) return;

        if (!chartInstance.current) {
            chartInstance.current = echarts.init(chartRef.current);
        }

        chartInstance.current.setOption(options);

        const handleResize = () => {
            chartInstance.current?.resize();
        };

        window.addEventListener("resize", handleResize);

        return () => {
            window.removeEventListener("resize", handleResize);
            chartInstance.current?.dispose();
        };
    }, [options]);

    return <div ref={chartRef} style={{ width: "100%", height: "400px" }} />;
}