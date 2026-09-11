import { ArrowLeft, ArrowRight, Quote } from "lucide-react";
import Image from "next/image";
import Link from "next/link";




export default function Testimonial() {
    return (
        <section className="bg-[#121012] w-full py-16 md:py-30 px-[5%] lg:px-[14%] flex flex-col items-start  gap-6 " >


            <h3 className=" text-3xl md:text-5xl font-medium leading-[114%] text-[#ffffff] md:w-[80%] font-season-vf ">Building trust at every step of verification</h3>

            <Link href={"#"} className="font-modern_era_mono pb-0.5 text-sm md:text-base border-white  border-b " >  READ CUSTOMER STORIES </Link>

            <div className="w-full flex items-end justify-end flex-col gap-0 my-5 "  >
                <span className="size-14 bg-white flex items-center justify-center text-black " >
                    <Quote fill="#000000SSS" size={20} />
                </span>
                <hr className=" w-full bg-white/20 h-[0.5px] " />
            </div>




            <div className=" w-full h-full md:h-[55vh]  flex flex-col md:flex-row items-center justify-between gap-10 md:gap-28 p-1 "  >

                <div className=" md:basis-[33%] w-full h-75 md:h-[90%]  rounded-sm overflow-hidden relative " >
                    <Image
                        src={"/people/mr-chidera.webp"}
                        alt={`TheGreyIT Educational Consults`}
                        fill
                        className="h-full w-full top-0 left-0 absolute object-center object-cover "
                    />
                </div>



                <div className=" md:basis-[67%] w-full h-[85%]   flex flex-col items-start gap-7 " >


                    <Image
                        src={"/logos/THEGREYAElogoBlack.webp"}
                        alt="logo"
                        width={200} height={200}
                        className="w-[120px] md:w-[200px] " />



                    <p className="font-uncut text-base md:text-2xl  text-left font-normal gap-3 md:mt-10 " >CivicVerify AI makes verification simple.
                        The process is seamless, the results are accurate, and most importantly,
                        it gives us confidence in every document we verify.</p>


                    <Link href={"#"} className="font-modern_era_mono pb-0.5 text-sm md:text-base border-white  border-b " >
                        READ CUSTOMER STORIES </Link>


                    <div className="mt-auto w-full flex flex-col gap-4 md:flex-row items-end md:items-center justify-between font-modern_era_mono " >
                        <div className=" border border-white/30 py-1.5 px-2 md:px-4 rounded-sm uppercase text-xs md:text-base text-white " >
                            <span className="text-white opacity-70" > Chidera Abel </span>| Managing Director @ TheGreyIT
                        </div>


                        <div className="w-fit flex items-center justify-center gap-2 " >
                            <button className=" group rounded-sm cursor-pointer  relative size-10" >
                                <span className="border border-white/30  group-hover:scale-85 absolute top-0 left-0 h-full w-full
                                  rounded-sm transform transition-all duration-200 " />


                                <ArrowLeft size={16} className="absolute top-[50%] left-[50%] translate-y-[-50%] translate-x-[-50%] " />
                            </button>



                            <button className=" group rounded-sm cursor-pointer  relative size-10" >
                                <span className="border border-white/30  group-hover:scale-85 absolute top-0 left-0 h-full w-full
                                  rounded-sm transform transition-all duration-200 " />


                                <ArrowRight size={16} className="absolute top-[50%] left-[50%] translate-y-[-50%] translate-x-[-50%] " />
                            </button>
                        </div>
                    </div>

                </div>

            </div>


        </section>
    )
}