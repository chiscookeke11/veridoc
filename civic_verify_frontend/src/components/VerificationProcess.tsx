import { ArrowRight, Check } from "lucide-react";
import StepTracker from "./StepTracker";




export default function VerificationProcess() {
    return (
        <div className=" w-full max-w-4xl h-[200px]  flex items-center justify-between gap-4  font-uncut "  >

            <div className=" md:basis-[40%]  w-full h-full rounded-sm flex flex-col justify-between gap-10
             p-3 bg-[#151312] text-white
              " >

                <div className="flex justify-between items-center " >
                    <div className="space-y-1.5 " >
                        <h5 className=" tracking-wide text-lg " >Identity Document</h5>
                        <p className="text-xs font-normal " >NIN:
                            <span className="px-1.5 py-1 bg-[#211E1C] ml-2 font-sans rounded-sm " >123-4567-8901</span>
                        </p>
                    </div>

                    <StepTracker
                        currentStep={4}
                        totalSteps={5}
                    />
                </div>


                <div className="space-y-1.5  ">
                    <h4 className="text-5xl font-mono " >67%</h4>
                    <p className="uppercase text-xs font-mono text-white/40 " >VERIFICATION IN PROGRESS...</p>
                </div>

            </div>


            {/* Rating  */}
            <div className=" w-full hidden md:flex md:basis-[25%]  h-full rounded-sm flex-col justify-between gap-2
             p-3 bg-white text-[#131313] border  border-black/20  " >
                <h6 className="font-mono text-sm font-medium " >AI VERIFICATION</h6>

                <div className="size-32 border-3 border-b-transparent border-[#384ce3] mx-auto  rounded-full
                shrink-0 flex flex-col items-center justify-center  gap-1 " >

                    <h4 className="text-5xl font-mono text-[#384ce3] font-semibold " >A+</h4>
                    <small className="text-[#131313] font-mono text-[9px] font-medium " >Highly Authentic</small>

                </div>

            </div>


            <div className="  w-full hidden md:flex md:basis-[35%]  h-full rounded-sm flex-col justify-between gap-1
             p-3 bg-white text-[#131313] border  border-black/20 font-uncut " >

                <div className="w-full flex items-center justify-between " >
                    <span className="text-[#686469] text-sm font-medium " > Document  </span>
                    <span className="px-2 py-1 bg-[#E2EDFA] text-sm font-sans rounded-xs flex items-center gap-1.5 ">
                        <Check size={15} />
                        Authentic </span>
                </div>

                <hr className="border-[0.5px]  border-black/10" />


                <div className="w-full flex items-center justify-between " >
                    <span className="text-[#686469] text-sm font-medium " >  Identity </span>
                    <span className="px-2 py-1 bg-[#E5F7EC] text-sm font-sans rounded-xs flex items-center gap-1.5 ">
                        <Check size={15} />
                        Verified    </span>
                </div>

                <hr className="border-[0.5px]  border-black/10" />

                <div className="w-full flex items-center justify-between " >
                    <span className="text-[#686469] text-sm font-medium " > Tampering   </span>
                    <span className="px-2 py-1 bg-[#E2EDFA] text-sm font-sans rounded-xs flex items-center gap-1.5 ">
                        <Check size={15} />
                        No issues</span>
                </div>


                <hr className="border-[0.5px]  border-black/10" />


                <div className="w-full flex items-center justify-between text-[#384ce3] font-semibold tracking-wide ">
                    See full report

                    <ArrowRight size={16} />
                </div>

            </div>

        </div>
    )
}