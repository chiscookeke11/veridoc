import { ArrowDownToLine, Plus } from "lucide-react";
import CustomButton from "./ui_components/CustomButton";
import DocumentScanner from "./document_scanner_component/DocumentScanner";



export default function Hero() {
    return (
        <section className=" mx-[4%] md:mx-[13%] h-screen flex flex-col items-center justify-center gap-0  "   >


            <div className="h-full basis-1/2 w-full flex items-center justify-center flex-col gap-8 relative
            border-b-[0.5px]  border-white/10  border-r-[0.5px] border-l-[0.5px]
            " >
                <h1 className=" w-full max-w-2xl text-3xl md:text-7xl text-center font-season-vf leading-[120%] " >Building trust through verified identity</h1>


                <CustomButton
                    className="font-modern_era_mono uppercase text-sm bg-[#384ce3]! text-white "
                    variant="primary"
                    icon={<ArrowDownToLine size={16} />}
                >
                    Download Desktop App
                </CustomButton>


                <span className=" size-8 bg-[#071c3f] absolute bottom-[-14px] right-[-10px] md:right-[-16px] rounded-full flex items-center justify-center" >
                    <Plus size={22} />
                </span>
                <span className=" size-8 bg-[#071c3f] absolute bottom-[-14px] left-[-10px] md:left-[-16px] rounded-full flex items-center justify-center " >
                    <Plus size={22} />
                </span>
            </div>


            <div className=" h-full basis-1/2 w-full flex items-center justify-center flex-col  border-b-[0.5px]  border-white/10  border-r-[0.5px] border-l-[0.5px] " >

                <DocumentScanner />

            </div>


        </section>
    )
}