import { VestaboardGrid } from "@/components/VestaboardGrid";
import { InstallableManager } from "@/components/InstallableManager";

export default function Home() {
  return (
    <main className="min-h-screen py-8">
      <div className="w-full max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <VestaboardGrid />
          </div>
          <div className="lg:col-span-1">
            <InstallableManager />
          </div>
        </div>
      </div>
    </main>
  );
}
