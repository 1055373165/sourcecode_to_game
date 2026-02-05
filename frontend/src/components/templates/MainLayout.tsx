/**
 * Main layout component with Header and Sidebar
 */
import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from '../organisms/Header/Header';
import { Sidebar } from '../organisms/Sidebar/Sidebar';

export function MainLayout() {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-purple-900/20">
            <Header />
            <div className="flex">
                <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
                <main className="flex-1 lg:ml-0 min-h-[calc(100vh-4rem)]">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
