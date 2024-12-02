import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { LayoutDefault } from './layout-default/layout-default.component';
import { HomeComponent } from '../home/home.component';
import { CartCheckoutComponent } from '../cart-checkout/cart-checkout.component';
import { OrderCheckoutComponent } from '../order-checkout/order-checkout.component';
import { TncProfileComponent } from '../tnc-profile/tnc-profile.component';
import { OrderHistoryComponent } from '../tnc-profile/order-history/order-history.component';
import { PersonalInfoComponent } from '../tnc-profile/personal-info/personal-info.component';
import { ChangePasswordComponent } from '../tnc-profile/change-password/change-password.component';
import { CartCheckout2Component } from '../cart-checkout2/cart-checkout2.component';
import { ProductListComponent } from '../product/product-list/product-list.component';

export const LayoutRoutes: Routes = [
  // {
  //   path: 'orderCheckout',
  //   component: OrderCheckoutComponent
  // },
  {
    path: 'profile',
    component: TncProfileComponent,
    children: [
      { path: '', component: OrderHistoryComponent },
      { path: 'history', component: OrderHistoryComponent },
      { path: 'personalInfo', component: PersonalInfoComponent },
      { path: 'change-password', component: ChangePasswordComponent},
    ]
    // loadChildren: () => import('../tnc-profile/tnc-profile.module').then((m) => m.TncProfileModule)
  },
  {
    path: '',
    component: LayoutDefault,
    children: [
      { path: '', component: HomeComponent },
      {
        path: 'product',
        loadChildren: () =>
          import('../product/product.module').then((m) => m.ProductModule),
      },
      {
        path: 'cart',
        component: CartCheckoutComponent,
        // children: [],
      },
      {
        path: 'checkout',
        component: CartCheckout2Component,
      },
      {
        path: 'category/:categoryname',
        component: ProductListComponent
      }
    ],
  },
  {
    path: 'orderCheckout',
    component: OrderCheckoutComponent,
  },
];

@NgModule({
  imports: [RouterModule.forChild(LayoutRoutes)],
  exports: [RouterModule],
})
export class LayoutRoutingModule {}
