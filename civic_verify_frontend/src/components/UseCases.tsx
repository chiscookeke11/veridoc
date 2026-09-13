"use client"

import { Plus } from "lucide-react";
import { use_cases_data } from "../../data/use_cases_data";
import { useState } from "react";
import Image from "next/image";
import { motion } from "framer-motion"



export default function UseCases() {
    const [selected, setSelected] = useState(0)


    return (
        <section className="w-full max-w-7xl  mx-auto relative text-black font-season-vf pb-12 md:pb-52 px-8 " >

            <div className="w-full h-px bg-black/10" />

            <span className="  absolute -top-2.5 left-0 " >
                <Plus size={20} color="#071c3f" />
            </span>




            <div className="w-full flex items-stretch justify-between gap-20  mt-8 " >


                {/* The use case text  */}
                <div className=" md:basis-1/2 w-full h-full flex flex-col items-start gap-5 py-4 " >

                    <h5 className=" text-xs font-modern_era_mono text-[#000000] md:text-base " >USE CASES</h5>
                    <h3 className=" text-2xl md:text-5xl font-medium leading-[114%] text-[#000000] md:w-[80%] " >Identity verification for every digital workflow</h3>


                    {/* Accordion  */}
                    <div className=" w-full flex h-full flex-col items-start gap-5 " >

                        {/* accordion drawer */}
                        {use_cases_data.map((use_case, i) => (
                            <div
                                onClick={() => setSelected(i)}
                                key={i} className={`group w-full border-black/10 py-2 cursor-pointer ${i === 0 ? " border-t border-b " : "border-b"}`} >

                                {/* accordion head  */}
                                <div className="w-full py-2.5 px-1 flex items-center justify-start gap-4 "  >

                                    <Image
                                        src={use_case.icon}
                                        alt="icon"
                                        width={1000}
                                        height={1000}
                                        className="size-6 "
                                    />

                                    <h4 className="font-season-vf font-medium text-lg md:text-[22px] " > {use_case.title} </h4>
                                </div>

                                {/* accordion body  */}
                                <div
                                    className={`overflow-hidden font-uncut text-sm md:text-xl text-[#000000] opacity-70
    ${selected === i ? "h-60 max-h-fit py-1" : "h-0 py-0"}
    duration-300 ease-in-out transition-all`}
                                >
                                    {selected === i && (
                                        <motion.p
                                            key={selected}
                                            initial={{
                                                y: 30,
                                                opacity: 0,
                                            }}
                                            animate={{
                                                y: 0,
                                                opacity: 1,
                                            }}
                                            transition={{
                                                duration: 0.5,
                                                ease: [0.22, 1, 0.36, 1],
                                            }}
                                        >
                                            {use_case.content}
                                        </motion.p>
                                    )}
                                </div>
                            </div>
                        ))}

                    </div>


                </div>




                {/* The use case image */}
                <div className=" hidden md:flex basis-1/2 bg-amber-300 self-stretch overflow-hidden " >

                    <Image
                        src={use_cases_data[selected].image}
                        alt={use_cases_data[selected].title}
                        height={500} width={500}
                        className="object-cover object-center w-full h-full  "
                    />

                </div>

            </div>



        </section >
    )
}