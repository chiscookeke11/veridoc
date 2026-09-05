import { Check } from "lucide-react";




export default function VerificationResult() {
    return (
        <div className="flex items-center flex-col gap-5 " >
            <div className=" size-44 bg-green-700 rounded-full  flex items-center justify-center text-white " >
                <Check size={100} />

            </div>

            <p className=" text-4xl text-[#384ce3] font-season-vf   ">
                Authentic </p>
        </div>
    )
}