"use client"


import { motion } from "framer-motion"



export default function EmpowerCTA() {
    return (
        <section className="w-full max-w-7xl  mx-auto relative text-black font-season-vf flex items-center justify-center py-12 md:py-52 px-8  " >
            <motion.h3
                initial={{
                    opacity: 0
                }}
                whileInView={{
                    opacity: 1
                }}

                viewport={{
                    once: true,
                    amount: 0.6
                }}

                transition={{
                    duration: 1,
                    ease: "easeInOut"
                }}

                className="text-center text-4xl md:text-7xl font-medium " >
                Empower your teams with AI to make smarter decisions, faster.
            </motion.h3>


        </section>
    )
}