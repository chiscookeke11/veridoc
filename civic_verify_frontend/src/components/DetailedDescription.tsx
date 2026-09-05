"use client"

import { Plus } from "lucide-react";
import VerificationProcess from "./VerificationProcess";
import { motion, useScroll, useTransform } from "framer-motion"
import { useRef } from "react";
import VerificationResult from "./ui_components/VerificationResult";



export default function DetailedDescription() {

    const targetRef = useRef<HTMLDivElement>(null)
    const { scrollYProgress } = useScroll({
        target: targetRef,
        offset: ["start end", "end start"]
    })




    const x = useTransform(
        scrollYProgress,
        [0, 1],
        ["100%", "-160%"]
    );


    const processOpacity = useTransform(
        scrollYProgress,
        [0, 0.5, 0.55],
        [1, 1, 0]
    );

    const resultOpacity = useTransform(
        scrollYProgress,
        [0.4, 0.75, 1],
        [0, 1, 1]
    );





    return (
        <section ref={targetRef} className="w-full max-w-7xl  mx-auto relative md:min-h-[50vh] py-20 md:py-80 px-8
        flex items-center justify-center flex-col gap-16  overflow-hidden " >

            {/* corners */}
            <span className="  absolute bottom-0 right-0 " >
                <Plus size={22} color="#071c3f" />
            </span>

            <span className="  absolute top-0 right-0 " >
                <Plus size={22} color="#071c3f" />
            </span>


            <span className="  absolute bottom-0 left-0 " >
                <Plus size={22} color="#071c3f" />
            </span>

            <span className="  absolute top-0 left-0 " >
                <Plus size={22} color="#071c3f" />
            </span>



            <h3 className="text-center text-black font-season-vf font-medium text-2xl md:text-5xl max-w-4xl leading-[120%] mb-4 " >
                One platform for identity and document verification, built for the digital economy.</h3>

            <div className="relative w-full min-h-[400px] flex items-center justify-center">
                {/* Verification Process */}
                <motion.div
                    style={{ opacity: processOpacity }}
                    className="absolute inset-0 flex items-center justify-center"
                >
                    <VerificationProcess />
                </motion.div>

                {/* Verification Result */}
                <motion.div
                    style={{ opacity: resultOpacity }}
                    className="absolute inset-0 flex items-center justify-center"
                >
                    <VerificationResult />
                </motion.div>
            </div>




            {/* Scroll transition */}
            <motion.span
                style={{
                    x,
                }}
                className="
        absolute
        top-0
        left-0
        w-full
        h-full
        pointer-events-none
        z-20
        border-l-2
        border-[#384ce3]
        bg-gradient-to-r
        from-[#384ce3]/30
        via-[#ffffff]/10
    "
            />



        </section >
    )
}