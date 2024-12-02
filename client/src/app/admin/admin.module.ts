import { NgModule } from '@angular/core';
import { MainLayoutComponent } from './layouts/main-layout/main-layout.component';
import { SubTableComponent } from './layouts/components/sub-table/sub-table.component';
import { DashboardComponent } from './layouts/dashboard/dashboard.component';
import { NavMenuComponent } from './layouts/components/nav-menu/nav-menu.component';
import { HeaderComponent } from './layouts/components/header/header.component';
import { MainTableComponent } from './layouts/components/main-table/main-table.component';
import { AdminRoutingModule } from './admin-routing.module';
import { CommonModule } from '@angular/common';
import { GridModule } from '@progress/kendo-angular-grid';
import { ButtonsModule } from '@progress/kendo-angular-buttons';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { DialogsModule } from '@progress/kendo-angular-dialog';
import { DropDownsModule } from '@progress/kendo-angular-dropdowns';

@NgModule({
  declarations: [
    DashboardComponent,
    NavMenuComponent,
    HeaderComponent,
    SubTableComponent,
    MainLayoutComponent,
    MainTableComponent
  ],
  imports: [
    CommonModule,
    AdminRoutingModule,
    GridModule,
    ButtonsModule,
    FormsModule,
    ReactiveFormsModule,
    DialogsModule,
    DropDownsModule
  ],
  exports: [
    DashboardComponent,
    NavMenuComponent,
    HeaderComponent,
    MainTableComponent,
    SubTableComponent,
    MainLayoutComponent,
  ]
})
export class AdminModule { }
