import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"

import { MainLayout } from "@/components/layout/MainLayout"
import { SessionListener } from "@/components/SessionListener"
import { ProtectedRoute, RequirePermission } from "@/routes/guards"
import { LoginPage } from "@/pages/auth/Login"
import { ForbiddenPage } from "@/pages/Forbidden"
import { DashboardPage } from "@/pages/dashboard/DashboardPage"
import { AssistantPage } from "@/pages/assistant/AssistantPage"
import { ProductsPage } from "@/pages/products/ProductsPage"
import { InventoryPage } from "@/pages/inventory/InventoryPage"
import { CustomersPage } from "@/pages/customers/CustomersPage"
import { SuppliersPage } from "@/pages/suppliers/SuppliersPage"
import { PurchasesPage } from "@/pages/purchases/PurchasesPage"
import { PosPage } from "@/pages/pos/PosPage"
import { SalesPage } from "@/pages/sales/SalesPage"
import { UsersPage } from "@/pages/users/UsersPage"
import { RolesPage } from "@/pages/roles/RolesPage"
import { StoresPage } from "@/pages/stores/StoresPage"
import { AnalyticsPage } from "@/pages/analytics/AnalyticsPage"
import { TerminalsPage } from "@/pages/terminals/TerminalsPage"
import { ShiftsPage } from "@/pages/shifts/ShiftsPage"
import { CashAccountsPage } from "@/pages/cash-accounts/CashAccountsPage"
import { AccountsPayablePage } from "@/pages/accounts-payable/AccountsPayablePage"
import { AccountsReceivablePage } from "@/pages/accounts-receivable/AccountsReceivablePage"
import { CountriesPage } from "@/pages/countries/CountriesPage"
import { StatesPage } from "@/pages/states/StatesPage"
import { MunicipalitiesPage } from "@/pages/municipalities/MunicipalitiesPage"
import { SpecialtiesPage } from "@/pages/specialties/SpecialtiesPage"

export default function App() {
  return (
    <BrowserRouter>
      <SessionListener />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/403" element={<ForbiddenPage />} />

        <Route
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<DashboardPage />} />

          <Route
            path="/assistant"
            element={
              <RequirePermission permission="assistant:use">
                <AssistantPage />
              </RequirePermission>
            }
          />

          <Route
            path="/pos"
            element={
              <RequirePermission permission="sale:create">
                <PosPage />
              </RequirePermission>
            }
          />

          <Route
            path="/sales"
            element={
              <RequirePermission permission="sale:read">
                <SalesPage />
              </RequirePermission>
            }
          />

          <Route
            path="/products"
            element={
              <RequirePermission permission="product:read">
                <ProductsPage />
              </RequirePermission>
            }
          />
          <Route
            path="/inventory"
            element={
              <RequirePermission permission="inventory:read">
                <InventoryPage />
              </RequirePermission>
            }
          />
          <Route
            path="/customers"
            element={
              <RequirePermission permission="customer:read">
                <CustomersPage />
              </RequirePermission>
            }
          />
          <Route
            path="/suppliers"
            element={
              <RequirePermission permission="supplier:read">
                <SuppliersPage />
              </RequirePermission>
            }
          />
          <Route
            path="/purchases"
            element={
              <RequirePermission permission="purchase:read">
                <PurchasesPage />
              </RequirePermission>
            }
          />
          <Route
            path="/stores"
            element={
              <RequirePermission permission="store:read">
                <StoresPage />
              </RequirePermission>
            }
          />
          <Route
            path="/users"
            element={
              <RequirePermission permission="user:read">
                <UsersPage />
              </RequirePermission>
            }
          />
          <Route
            path="/roles"
            element={
              <RequirePermission permission="role:read">
                <RolesPage />
              </RequirePermission>
            }
          />

          <Route
            path="/analytics"
            element={
              <RequirePermission permission="analytics:read">
                <AnalyticsPage />
              </RequirePermission>
            }
          />
          <Route
            path="/terminals"
            element={
              <RequirePermission permission="pos_terminal:create">
                <TerminalsPage />
              </RequirePermission>
            }
          />
          <Route
            path="/shifts"
            element={
              <RequirePermission permission="shift:open">
                <ShiftsPage />
              </RequirePermission>
            }
          />
          <Route
            path="/cash-accounts"
            element={<CashAccountsPage />}
          />
          <Route
            path="/accounts-payable"
            element={
              <RequirePermission permission="accounts:create">
                <AccountsPayablePage />
              </RequirePermission>
            }
          />
          <Route
            path="/accounts-receivable"
            element={
              <RequirePermission permission="accounts:create">
                <AccountsReceivablePage />
              </RequirePermission>
            }
          />
          <Route path="/countries" element={<CountriesPage />} />
          <Route path="/states" element={<StatesPage />} />
          <Route path="/municipalities" element={<MunicipalitiesPage />} />
          <Route path="/specialties" element={<SpecialtiesPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
