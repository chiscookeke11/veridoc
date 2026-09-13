import Link from "next/link";



export default function Footer() {
    return (
        <footer className="w-full bg-white  flex items-center justify-center pt-36 pb-10 px-[5%]  " >



            <div className=" max-w-7xl w-full flex  flex-col gap-16 items-start  " >

                <ul className="w-full flex flex-col md:flex-row md:items-center gap-7 md:gap-15 text-sm font-uncut text-black  " >
                    <li className=" opacity-70 hover:opacity-100 duration-300 ease-in-out transition-all " ><Link href={"#"} >Terms of Use</Link></li>
                    <li className=" opacity-70 hover:opacity-100 duration-300 ease-in-out transition-all "><Link href={"#"} >Privacy Policy</Link></li>
                    <li className=" opacity-70 hover:opacity-100 duration-300 ease-in-out transition-all "><Link href={"#"} >Cookies</Link></li>
                </ul>

            </div>


        </footer>
    )
}