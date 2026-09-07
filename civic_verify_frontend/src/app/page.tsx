import DetailedDescription from "@/components/DetailedDescription";
import EmpowerCTA from "@/components/EmpowerCTA";
import Hero from "@/components/Hero";
import TrustedCompanies from "@/components/TrustedCompanies";
import UseCases from "@/components/UseCases";


export default function Home() {
  return (
    <div>
      <Hero />
      <TrustedCompanies />
      <div className="bg-white py-10 flex flex-col items-center justify-center gap-12 " >
        <DetailedDescription />
        <EmpowerCTA />
        <UseCases />
      </div>
    </div>
  );
}
