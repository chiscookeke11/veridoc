import Image from "next/image";
import Link from "next/link";



export default function AppLogo() {
    return (
        <Link href={"/"} >
            <Image
                className=" w-[100px] md:w-[180px] aspect-auto "
                src={"/logos/logo3.png"}
                alt="logo"
                width={180}
                height={100} />
        </Link>
    )
}