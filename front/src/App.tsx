import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"

import { MainLayout } from "@/components/layout/MainLayout"
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

export default function App() {
  return (
    <BrowserRouter>
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
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
