import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule, HttpClientXsrfModule } from '@angular/common/http';
import { MainLayoutComponent } from './layouts/main-layout/main-layout.component';
import { MinimizedBarComponent } from './layouts/components/minimized-bar/minimized-bar.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MessageComponent } from './layouts/components/message/message.component';
import { ChatComponent } from './layouts/components/chat/chat.component';

@NgModule({
  declarations: [
    MainLayoutComponent,
    MinimizedBarComponent,
    MessageComponent,
    ChatComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientXsrfModule.withOptions({
      cookieName: 'csrf_access_token',
      headerName: 'X-CSRF-TOKEN',
    }),
  ],
  exports: [MainLayoutComponent,MinimizedBarComponent,
    MessageComponent,
    ChatComponent],
})

export class ChatModule {}