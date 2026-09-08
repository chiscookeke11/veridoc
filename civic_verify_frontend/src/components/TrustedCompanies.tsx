import Link from "next/link";
import Marquee from "react-fast-marquee";
import { trusted_organizations_data } from "../../data/trusted_organizations_data";
import Image from "next/image";




export default function TrustedCompanies() {

    return (
        <section className="w-full bg-white py-20 md:py-44 px-[4%] text-black flex flex-col items-center justify-center gap-5  " >

            <h3 className="text-center font-season-vf font-medium text-2xl md:text-5xl max-w-4xl leading-[120%] mb-4 " >Trusted by organizations that rely on secure identity and document verification</h3>


            <Link href={"#"} className="font-modern_era_mono font-medium text-sm md:text-base group"  >
                READ ALL CUSTOMER STORIES

                <hr className="mt-2 group border-black/10 " />
            </Link>


            <div className="w-full max-w-7xl flex items-center justify-center mt-16 font-season-vf relative "  >
                <Marquee speed={100} >
                    {trusted_organizations_data.map((org, i) => (
                        <div key={i} title={org.name}  >
                            <Image
                                src={org.image}
                                alt={`${org.name}-logo`}
                                width={200} height={200}
                                className="w-[120px] md:w-[200px] "
                            />
                        </div>
                    ))}
                </Marquee>


                {/* blur */}
                <span
                    className="
        pointer-events-none
        absolute
        inset-y-0
        left-0
        w-24
        md:w-40
        bg-gradient-to-r
        from-white
        via-white/80
        to-transparent
        z-10
    "
                />

                {/* Right fade */}
                <span
                    className="
        pointer-events-none
        absolute
        inset-y-0
        right-0
        w-24
        md:w-40
        bg-gradient-to-l
        from-white
        via-white/80
        to-transparent
        z-10
    "
                />




            </div>



            {/* Detailed organization Testimonial */}

            <div className="w-full max-w-7xl grid grid-cols-1  md:grid-cols-2 mt-10 place-items-center justify-center gap-4
             min-h-[450px]   " >



                <div className="w-full  h-full grid grid-cols-1 md:grid-cols-2 place-items-center justify-center py-3 px-1.5 gap-3  border-b border-t border-black/10  " >


                    <div className="w-full h-full flex flex-col items-start justify-between py-4 md:py-8 gap-5 md:gap-0 " >

                        <Image
                            src={"/logos/THEGREYAElogoBlack.webp"}
                            alt="logo"
                            width={200} height={200}
                            className="w-[120px] md:w-[200px] " />

                        <p className="font-uncut text-lg md:text-2xl  text-left font-normal " >CivicVerify AI makes verification simple.
                            The process is seamless, the results are accurate, and most importantly,
                            it gives us confidence in every document we verify.</p>

                        <Link href={"#"} className="font-modern_era_mono font-medium text-sm md:text-base group"  >
                            READ FULL STORY

                            <hr className="mt-2 group border-black/30 " />
                        </Link>
                    </div>

                    <div className="w-full h-full overflow-hidden rounded-lg group ">
                        <Image
                            src={"/people/mr-chidera.webp"}
                            alt={`TheGreyIT Educational Consults`}
                            width={200} height={200}
                            className="h-full w-full object-center object-cover group-hover:scale-110 duration-300 ease-in-out transform cursor-pointer "
                        />
                    </div>

                </div>


                <div className="w-full h-full grid grid-cols-2 place-items-center justify-center gap-3" >

                    <div className="w-full h-full flex flex-col items-start justify-between py-9 px-3 md:px-6 bg-[#eff5f0] rounded-sm gap-6 md:gap-0" >

                        <div className=" space-y-4 md:space-y-8 " >
                            <h4 className="font-modern_era_mono uppercase text-xs md:text-[15px] font-semibold tracking-wide " >Reduction in manual reviews</h4>
                            <h5 className="font-uncut text-4xl md:text-[64px]  font-semibold " >60%</h5>
                        </div>



                        <Image
                            src={"/logos/THEGREYAElogoBlack.webp"}
                            alt="logo"
                            width={200} height={200}
                            className="w-[120px] md:w-[200px] " />

                    </div>



                    <div className="w-full h-full flex flex-col items-start justify-between py-9 px-3 md:px-6   border-b border-t border-black/10 gap-6 md:gap-0" >

                        <div className=" space-y-4 md:space-y-8 " >
                            <h4 className="font-modern_era_mono uppercase text-xs md:text-[15px] font-semibold tracking-wide " >Reduction in manual reviews</h4>
                            <h5 className="font-uncut text-4xl md:text-[64px] font-semibold " >60%</h5>
                        </div>



                        <Image
                            src={"/logos/THEGREYAElogoBlack.webp"}
                            alt="logo"
                            width={200} height={200}
                            className="w-[120px] md:w-[200px] " />

                    </div>


                </div>

            </div>




        </section>
    )
}