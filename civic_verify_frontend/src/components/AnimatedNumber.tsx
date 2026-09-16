"use client"

import { useEffect, useState } from "react"
import { motion, useInView } from "framer-motion"
import { useRef } from "react"



interface AnimatedNumberProps {
    value: number,
    duration?: number
}


export default function AnimatedNumber({ value, duration = 1.5 }: AnimatedNumberProps) {
    const ref = useRef(null)
    const isInView = useInView(ref, {
        once: true,
        amount: 0.5,
    })

    const [count, setCount] = useState(0)

    useEffect(() => {
        if (!isInView) return

        let start = 0
        const end = value
        const startTime = performance.now()

        const animate = (currentTime: number) => {
            const elapsed = currentTime - startTime
            const progress = Math.min(elapsed / (duration * 1000), 1)

            // Ease out animation
            const easedProgress = 1 - Math.pow(1 - progress, 3)

            start = Math.round(easedProgress * end)
            setCount(start)

            if (progress < 1) {
                requestAnimationFrame(animate)
            }
        }

        requestAnimationFrame(animate)
    }, [isInView, value, duration])

    return (
        <motion.span ref={ref}>
            {count}%
        </motion.span>
    )
}