import { NavLink } from 'react-router-dom'
import { ChevronDown } from 'lucide-react'
import { useMemo } from 'react'

import { useAuth } from '../auth/AuthContext'
import { filterMenuByRole, getMenuIcon, menuConfig } from '../menu/menu'
import type { MenuItem } from '../types'
import { Logo } from '../components/ui/brand'

function MenuLink({ item, onClick }: { item: MenuItem; onClick: () => void }) {
  if (!item.path) return null
  const Icon = getMenuIcon(item.icon)

  return (
    <NavLink
      to={item.path}
      onClick={onClick}
      className={({ isActive }) =>
        `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
          isActive
            ? 'bg-brand-600 text-white'
            : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
        }`
      }
    >
      <Icon className="h-4.5 w-4.5 shrink-0" />
      <span className="truncate">{item.label}</span>
    </NavLink>
  )
}

function MenuGroup({
  item,
  onNavigate,
}: {
  item: MenuItem
  onNavigate: () => void
}) {
  const children = item.children ?? []
  const Icon = getMenuIcon(item.icon)

  return (
    <div>
      <div className="flex items-center gap-3 px-3 py-2 text-sm font-semibold text-slate-500">
        <Icon className="h-4.5 w-4.5 shrink-0" />
        <span className="truncate">{item.label}</span>
        <ChevronDown className="ml-auto h-4 w-4 opacity-50" />
      </div>
      <div className="mt-0.5 space-y-0.5 border-l border-slate-200 pl-3">
        {children.map((child) => (
          <MenuLink key={child.id} item={child} onClick={onNavigate} />
        ))}
      </div>
    </div>
  )
}

export function Sidebar({
  open,
  onClose,
}: {
  open: boolean
  onClose: () => void
}) {
  const { user } = useAuth()

  const items = useMemo(
    () => (user ? filterMenuByRole(menuConfig.items, user.role_name) : []),
    [user],
  )

  const handleNavigate = () => onClose()

  return (
    <>
      {/* Overlay en móvil */}
      {open ? (
        <div
          className="fixed inset-0 z-30 bg-slate-900/60 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      ) : null}

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-slate-200 bg-white transition-transform duration-200 lg:static lg:z-auto lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-16 shrink-0 items-center border-b border-slate-200 px-5">
          <Logo />
        </div>

        <nav className="flex-1 space-y-4 overflow-y-auto px-3 py-4" aria-label="Menú principal">
          {items.map((item) =>
            item.children ? (
              <MenuGroup key={item.id} item={item} onNavigate={handleNavigate} />
            ) : (
              <MenuLink key={item.id} item={item} onClick={handleNavigate} />
            ),
          )}
        </nav>

        <div className="border-t border-slate-200 px-5 py-4 text-xs text-slate-400">
          © {new Date().getFullYear()} POS · v0.1
        </div>
      </aside>
    </>
  )
}