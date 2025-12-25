import { VestaboardGrid } from "@/components/VestaboardGrid";
import { InstallableManager } from "@/components/InstallableManager";

export default function Home() {
  return (
    <main className="min-h-screen py-4 sm:py-8">
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex flex-col gap-4 sm:gap-6">
          <VestaboardGrid />
          <InstallableManager />
        </div>
      </div>
    </main>
  );
}
