import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { OrderHistoryComponent } from './order-history/order-history.component';
import { PersonalInfoComponent } from './personal-info/personal-info.component';
import { ChangePasswordComponent } from './change-password/change-password.component';

export const ProfileRoutes: Routes = [
  {
    path: '', component: OrderHistoryComponent
  },
  {
    path: 'history', component: OrderHistoryComponent
  },
  {
    path: 'personalInfo',
    component: PersonalInfoComponent,
  },
  {
    path: 'change-password',
    component: ChangePasswordComponent,
  }
];

@NgModule({
  imports: [RouterModule.forChild(ProfileRoutes)],
  exports: [RouterModule],
})
export class TncProfileRoutingModule { }