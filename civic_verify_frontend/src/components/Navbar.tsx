
import CustomButton from "./ui_components/CustomButton";
import AppLogo from "./ui_components/Logo";
import { ArrowDownToLine } from "lucide-react";




export default function Navbar() {
    return (
        <nav className="w-full flex items-center justify-between px-[4%] md:px-[13%] py-3 border-b-[0.5px]  border-white/10 font-uncut  " >
            <AppLogo />

            <ul className="hidden md:flex" >
                <li>Links</li>
            </ul>

        <CustomButton
                className="font-modern_era_mono uppercase text-sm md:text-base "
                variant="primary"
                icon={<ArrowDownToLine size={16} />}
            >Download
            </CustomButton>
        </nav>
    )
}