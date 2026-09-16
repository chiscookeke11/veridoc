"use client"


import { Plus } from "lucide-react";
import { StepData } from "../../data/steps_data";
import Image from "next/image";
import { motion, type Variants } from "framer-motion";



export default function AppWorkflow() {


    const containerVariants: Variants = {
        hidden: {},
        visible: {
            transition: {
                staggerChildren: 0.2,
            },
        },
    };

    const cardVariants: Variants = {
        hidden: {
            y: "200%",
        },
        visible: {
            y: 0,
            transition: {
                duration: 0.4,
                ease: "easeOut",
            },
        },
    };

    return (
        <section className="w-full max-w-7xl  mx-auto relative text-black font-season-vf
         pb-12 md:pb-52 px-8 flex flex-col items-start gap-4 overflow-hidden" >


            <h3 className=" text-3xl md:text-5xl font-medium leading-[114%] text-[#000000] md:w-[80%] ">AI-powered verification, from upload to decision</h3>
            <p className="font-uncut text-sm md:text-lg text-[#000000] opacity-70 lg:w-[50%] " >Upload your documents, let AI extract the details, and verify them against trusted data sources. All in one workflow.</p>



            <motion.div
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{
                    once: true,
                    amount: 0.2,
                }}
                className="mt-14 w-full relative  justify-center min-h-[60vh]  p-2
            grid grid-cols-1 md:grid-cols-3 place-items-center justify-items-center gap-5
            " >



                {/* corners */}
                <span className="  absolute -bottom-2.5 -right-2.5 " >
                    <Plus size={22} color="#071c3f" />
                </span>

                <span className="  absolute -top-2.5 -right-2.5 " >
                    <Plus size={22} color="#071c3f" />
                </span>


                <span className="  absolute -bottom-2.5 -left-2.5 " >
                    <Plus size={22} color="#071c3f" />
                </span>

                <span className="  absolute -top-2.5 -left-2.5 " >
                    <Plus size={22} color="#071c3f" />
                </span>




                {StepData.map((step, i) => (
                    <motion.div
                        variants={cardVariants}
                        style={{
                            backgroundColor: step.color,
                            color: "#ffffff"
                        }}
                        key={i}
                        className=" w-full  h-full rounded-md relative flex flex-col items-start px-3 py-5 md:p-5
                        font-uncut gap-2 md:gap-4 cursor-pointer group " >
                        <h4 className=" text-lg md:text-2xl font-medium " > {step.title} </h4>

                        <p className="font-uncut text-sm md:text-base text-[#ffffff] md:opacity-0 group-hover:opacity-70
                        md:translate-y-[20%] group-hover:translate-y-0 transition-all duration-400 ease-in-out

                        "> {step.description} </p>

                        <Image
                            src={step.img}
                            alt={`${step.title}-image`}
                            height={500} width={500}
                            className="absolute left-[50%] top-[50%] translate-x-[-50%] translate-y-[-50%]
                            w-[85%] h-[55%] object-center object-cover hidden md:block rounded-md
                             group-hover:translate-y-[-30%] group-hover:opacity-10 transition-all duration-400 ease-in-out  "
                        />

                        <div className="w-full mt-auto flex items-center justify-between  " >

                            <p className="text-[8px] md:text-xs font-modern_era_mono uppercase opacity-0
                            group-hover:opacity-100 transition-all duration-300 ease-in-out
                            " > {step.call_to_action} </p>

                            <span className="size-10 bg-white rounded-sm flex items-center justify-center
                            font-modern_era_mono font-bold text-lg md:text-xl text-black
                             " >
                                {i + 1}
                            </span>
                        </div>

                    </motion.div>
                ))}

            </motion.div>


        </section>
    )
}