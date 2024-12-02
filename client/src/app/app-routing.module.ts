import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MainLayoutComponent } from './admin/layouts/main-layout/main-layout.component';
import { LoginComponent } from './login/login.component';
import { AdminGuard } from './p-app/_helpers/admin.guard';

const routes: Routes = [
  {
    path: '',
    loadChildren: () =>
      import('../app/p-app/p-layout/p-layout.module').then(
        (m) => m.PLayoutModule
      ),
  },
  {
    path: 'admin',
    canActivate: [AdminGuard],
    component: MainLayoutComponent,
    loadChildren: () => import('./admin/admin.module').then((m) => m.AdminModule)
  },
  {
    path: 'login',
    component: LoginComponent
  }
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes, { scrollPositionRestoration: 'enabled' }),
  ], //back to top when route changed
  exports: [RouterModule],
})
export class AppRoutingModule {}
