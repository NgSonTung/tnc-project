import {
  NgModule,
  CUSTOM_ELEMENTS_SCHEMA,
  NO_ERRORS_SCHEMA,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { HomeComponent } from './home.component';
import { PLayoutModule } from '../p-layout/p-layout.module';
import { BoxProductModule } from '../p-layout/components/boxProduct/boxProduct.module';

@NgModule({
  declarations: [HomeComponent],
  imports: [CommonModule, PLayoutModule, BoxProductModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA],
  exports: [],
})
export class HomeModule { }
