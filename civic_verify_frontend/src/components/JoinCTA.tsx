import { Plus } from "lucide-react";
import CustomButton from "./ui_components/CustomButton";




export default function JoinCTA() {
    return (
        <section className="w-full bg-white py-20 md:py-32 px-5 md:px-10 flex items-center justify-center font-season-vf  " >



            <div className="w-full max-w-7xl bg-[#071c3f] py-10 md:py-16 px-6 md:px-10 rounded-md
             flex flex-col items-start justify-between gap-32 relative  group overflow-hidden
              " >


                <h3 className=" text-4xl md:text-7xl md:max-w-[50%] leading-[130%] z-10 " >Build trust with every verification</h3>


                <CustomButton
                    className="uppercase font-modern_era_mono  text-sm bg-[#384ce3]! text-white z-10"
                    variant="primary"
                    icon={<Plus size={16} />}
                >
                    Download Desktop App</CustomButton>



                <div
                    className="
        absolute
        h-full
        top-0
        right-0
        w-[200%]
        translate-x-[90%]
        group-hover:translate-x-0
        duration-400
        ease-in-out
        transition-transform
        z-0
    "
                >
                    {/* LEFT GRID */}
                    <div
                        className="
            absolute
            top-0
            left-0
            w-[13%]
            h-full
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

                    {/* RIGHT GRID */}
                    <div
                        className="
            absolute
            top-0
            right-0
            w-[13%]
            h-full
            pointer-events-none
            opacity-40
            bg-[length:16px_16px]
            md:bg-[length:26px_26px]
        "
                        style={{
                            backgroundImage: `
                url("data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12 8v8M8 12h8' stroke='%23ffffff' stroke-width='1' stroke-linecap='round'/%3E%3C/svg%3E")
            `,
                        }}
                    />
                </div>
            </div>


        </section>
    )
}