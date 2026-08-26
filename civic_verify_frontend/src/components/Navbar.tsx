import Link from "next/link";
import CustomButton from "./ui_components/CustomButton";




export default function Navbar() {
    return (
        <nav className="w-full flex items-center justify-between px-[6%] md:px-[13%] py-5 border-b-[0.5px]  border-white/10 font-uncut  " >
            <Link href={"/"} > Logo</Link>

            <ul>
                <li>Links</li>
            </ul>

            <CustomButton className="font-modern_era_mono" >Download </CustomButton>
        </nav>
    )
}