"use client";

import { Check } from "lucide-react";
import { useEffect, useState } from "react";

interface StepTrackerProps {
    currentStep: number;
    totalSteps: number;
    size?: number;
    strokeWidth?: number;
    activeColor?: string;
    trackColor?: string;
    textColor?: string;
}

export default function StepTracker({
    currentStep,
    totalSteps,
    size = 45,
    strokeWidth = 4,
    activeColor = "#384ce3",
    trackColor = "#292522",
    textColor = "#10182A",
}: StepTrackerProps) {
    const safeTotal = Math.max(totalSteps, 1);

    const clampedStep = Math.min(
        Math.max(currentStep, 0),
        safeTotal
    );

    const progress = clampedStep / safeTotal;

    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;

    const [animatedProgress, setAnimatedProgress] = useState(0);

    useEffect(() => {
        let animationFrame: number;
        const startTime = performance.now();
        const duration = 600;

        const animate = (currentTime: number) => {
            const elapsed = currentTime - startTime;
            const percentage = Math.min(elapsed / duration, 1);

            // Ease out
            const eased =
                1 - Math.pow(1 - percentage, 3);

            setAnimatedProgress(eased * progress);

            if (percentage < 1) {
                animationFrame =
                    requestAnimationFrame(animate);
            }
        };

        animationFrame =
            requestAnimationFrame(animate);

        return () => {
            cancelAnimationFrame(animationFrame);
        };
    }, [progress]);

    const strokeDashoffset =
        circumference * (1 - animatedProgress);

    return (
        <div
            className="relative flex items-center justify-center"
            style={{
                width: size,
                height: size,
            }}
        >
            <svg
                width={size}
                height={size}
                viewBox={`0 0 ${size} ${size}`}
                className="-rotate-90"
            >
                {/* Track */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={trackColor}
                    strokeWidth={strokeWidth}
                />

                {/* Progress */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={activeColor}
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={strokeDashoffset}
                />
            </svg>

            {/* Label */}
            <div
                className="absolute inset-0 flex items-center justify-center"
                style={{
                    color: textColor,
                }}
            >
                <span className="text-sm font-semibold">
                    <Check color="#ffffff" />
                </span>
            </div>
        </div>
    );
}