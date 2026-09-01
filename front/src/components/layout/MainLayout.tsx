import { useState } from "react"
import {
  NavLink,
  Outlet,
  useLocation,
  useNavigate,
} from "react-router-dom"
import {
  LayoutDashboard,
  ShoppingCart,
  Boxes,
  Users,
  Truck,
  Package,
  Store,
  ShieldCheck,
  Bot,
  LogOut,
  Menu,
  X,
  ChevronDown,
  ReceiptText,
  PackagePlus,
} from "lucide-react"

import { cn } from "@/lib/utils"
import { useAuthStore } from "@/store/authStore"
import { Button } from "@/components/ui"

type NavItem = {
  to: string
  label: string
  icon: React.ComponentType<{ className?: string }>
  permission?: string
}

const NAV_SECTIONS: { title: string; items: NavItem[] }[] = [
  {
    title: "Principal",
    items: [
      { to: "/", label: "Dashboard", icon: LayoutDashboard },
      {
        to: "/assistant",
        label: "Asistente IA",
        icon: Bot,
        permission: "assistant:use",
      },
      {
        to: "/pos",
        label: "Punto de Venta",
        icon: ShoppingCart,
        permission: "sale:create",
      },
      {
        to: "/sales",
        label: "Ventas",
        icon: ReceiptText,
        permission: "sale:read",
      },
    ],
  },
  {
    title: "Operación",
    items: [
      {
        to: "/products",
        label: "Productos",
        icon: Package,
        permission: "product:read",
      },
      {
        to: "/inventory",
        label: "Inventario",
        icon: Boxes,
        permission: "inventory:read",
      },
      {
        to: "/customers",
        label: "Clientes",
        icon: Users,
        permission: "customer:read",
      },
      {
        to: "/suppliers",
        label: "Proveedores",
        icon: Truck,
        permission: "supplier:read",
      },
      {
        to: "/purchases",
        label: "Entrada de mercancía",
        icon: PackagePlus,
        permission: "purchase:read",
      },
    ],
  },
  {
    title: "Administración",
    items: [
      {
        to: "/stores",
        label: "Tiendas",
        icon: Store,
        permission: "store:read",
      },
      {
        to: "/users",
        label: "Usuarios",
        icon: Users,
        permission: "user:read",
      },
      {
        to: "/roles",
        label: "Roles y Permisos",
        icon: ShieldCheck,
        permission: "role:read",
      },
    ],
  },
]

export function MainLayout() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const hasPermission = useAuthStore((s) => s.hasPermission)
  const navigate = useNavigate()
  const location = useLocation()

  const pageTitle =
    NAV_SECTIONS.flatMap((s) => s.items).find(
      (it) =>
        it.to !== "/" &&
        (location.pathname === it.to ||
          location.pathname.startsWith(it.to + "/")),
    )?.label ?? "Dashboard"

  const handleLogout = () => {
    setProfileOpen(false)
    logout()
    navigate("/login", { replace: true })
  }

  const sections = NAV_SECTIONS.map((sec) => ({
    ...sec,
    items: sec.items.filter(
      (it) => !it.permission || hasPermission(it.permission),
    ),
  })).filter((sec) => sec.items.length > 0)

  const sidebar = (
    <div className="flex h-full flex-col bg-slate-900 text-slate-300">
      <div className="flex h-16 items-center gap-2.5 px-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-lg shadow-brand-900/40">
          <ShoppingCart className="h-5 w-5" />
        </div>
        <div className="leading-tight">
          <span className="block text-[15px] font-bold tracking-tight text-white">
            POS Pro
          </span>
          <span className="block text-[11px] font-medium text-slate-400">
            Punto de venta
          </span>
        </div>
      </div>

      <nav className="flex-1 space-y-5 overflow-y-auto px-3 py-4">
        {sections.map((sec) => (
          <div key={sec.title}>
            <p className="mb-1 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
              {sec.title}
            </p>
            <div className="space-y-1">
              {sec.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  onClick={() => setMobileOpen(false)}
                  className={({ isActive }) =>
                    cn(
                      "group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-brand-500/15 text-white"
                        : "text-slate-300 hover:bg-slate-800/60 hover:text-white",
                    )
                  }
                >
                  {({ isActive }) => (
                    <>
                      <span
                        className={cn(
                          "absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-brand-400 transition-opacity",
                          isActive ? "opacity-100" : "opacity-0",
                        )}
                      />
                      <item.icon
                        className={cn(
                          "h-5 w-5 transition-colors",
                          isActive
                            ? "text-brand-300"
                            : "text-slate-400 group-hover:text-slate-200",
                        )}
                      />
                      {item.label}
                    </>
                  )}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      <div className="border-t border-slate-800 p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-700 text-sm font-bold text-white">
            {(user?.full_name || "U").charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-white">
              {user?.full_name}
            </p>
            <p className="truncate text-xs text-slate-400">
              {user?.role_name || "Usuario"}
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleLogout}
            className="ml-auto text-slate-400 hover:text-white hover:bg-slate-800"
            title="Cerrar sesión"
          >
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen">
      {/* Sidebar escritorio */}
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 lg:block">
        {sidebar}
      </aside>

      {/* Sidebar móvil */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div
            className="absolute inset-0 bg-slate-900/60"
            onClick={() => setMobileOpen(false)}
          />
          <div className="absolute inset-y-0 left-0 w-64">
            <button
              className="absolute right-3 top-4 z-10 text-slate-400"
              onClick={() => setMobileOpen(false)}
              aria-label="Cerrar menú"
            >
              <X className="h-6 w-6" />
            </button>
            {sidebar}
          </div>
        </div>
      )}

      <div className="lg:pl-64">
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-slate-200 bg-white px-4 sm:px-6">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setMobileOpen(true)}
            aria-label="Abrir menú"
          >
            <Menu className="h-6 w-6" />
          </Button>
          <div className="hidden sm:flex items-center gap-1.5 text-sm text-slate-500">
            <span className="font-semibold text-slate-800">POS Pro</span>
            <svg className="h-4 w-4 text-slate-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="m9 18 6-6-6-6" />
            </svg>
            <span className="text-slate-600">{pageTitle}</span>
          </div>
          <div className="ml-auto relative">
            <button
              onClick={() => setProfileOpen((v) => !v)}
              className="flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-slate-100"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-600 text-sm font-bold text-white">
                {(user?.full_name || "U").charAt(0).toUpperCase()}
              </div>
              <span className="hidden sm:block text-sm font-medium text-slate-700">
                {user?.full_name}
              </span>
              <ChevronDown className="h-4 w-4 text-slate-400" />
            </button>
            {profileOpen && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setProfileOpen(false)}
                />
                <div className="absolute right-0 z-20 mt-2 w-56 rounded-xl border border-slate-200 bg-white shadow-lg">
                  <div className="border-b border-slate-100 px-4 py-3">
                    <p className="text-sm font-semibold text-slate-800">
                      {user?.full_name}
                    </p>
                    <p className="text-xs text-slate-500">{user?.email}</p>
                    <span className="mt-1 inline-block rounded-full bg-brand-100 px-2 py-0.5 text-xs font-medium text-brand-700">
                      {user?.role_name}
                    </span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center gap-2 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50"
                  >
                    <LogOut className="h-4 w-4" /> Cerrar sesión
                  </button>
                </div>
              </>
            )}
          </div>
        </header>

        <main className="p-4 sm:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
