import DetailedDescription from "@/components/DetailedDescription";
import Hero from "@/components/Hero";
import TrustedCompanies from "@/components/TrustedCompanies";


export default function Home() {
  return (
    <div>
      <Hero />
      <TrustedCompanies />
      <div className="bg-white py-10 flex flex-col items-center justify-center gap-12 " >
        <DetailedDescription />
        <div className="w-full h-[300vh] "  >

        </div>
      </div>
    </div>
  );
}
