import { Plus } from "lucide-react";
import Image from "next/image";



export default function AssuranceSection() {
    return (
        <section className="w-full max-w-7xl  mx-auto relative text-black font-season-vf
         pb-12 md:pb-52 px-8 flex flex-col items-center gap-10
         " >

            <div className="w-full h-px bg-black/10" />

            <span className="absolute -top-2.5 left-0 " >
                <Plus size={20} color="#071c3f" />
            </span>


            <div className="w-full flex justify-between gap-10 items-center mt-8   "  >
                <div className=" space-y-2 md:space-y-5 w-full md:basis-1/2 " >
                    <h5 className=" text-xs font-modern_era_mono text-[#000000] md:text-base tracking-tight " >FRAUD PREVENTION</h5>
                    <h2 className=" text-3xl md:text-5xl font-medium leading-[114%] text-[#000000] md:w-[80%] ">Go beyond verification.</h2>
                </div>

                <div className="space-y-4 basis-1/2 hidden md:block " >
                    <div className="font-uncut text-xl font-medium text-[#000000]  " >AI Risk Intelligence</div>
                    <p className="font-uncut text-sm md:text-lg text-[#000000] opacity-70" > Analyze identity, document, and verification signals to uncover
                        suspicious activity and make more confident decisions.</p>
                </div>

            </div>


            <div
                className="
    relative w-full bg-[#BCA2CC]
    md:h-[65vh]
    rounded-md
    flex items-center justify-end
    pt-10
    overflow-hidden md:mt-5
  "
            >
                {/* Grid */}
                <div
                    className="
        absolute inset-0
        pointer-events-none
        opacity-40
        bg-[length:16px_16px]
        md:bg-[length:24px_24px]
    "
                    style={{
                        backgroundImage: `
            url("data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12 8v8M8 12h8' stroke='%23ffffff' stroke-width='1' stroke-linecap='round'/%3E%3C/svg%3E")
        `,
                    }}
                />

                <Image
                    src="/screen_images/a.png"
                    alt="app screen"
                    height={1000}
                    width={1000}
                    className="relative z-10 object-bottom object-contain h-full w-[90%] md:w-[80%] mx-auto"
                />
            </div>

        </section>
    )
}