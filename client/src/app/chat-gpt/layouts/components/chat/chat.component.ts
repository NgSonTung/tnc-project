import {
  Component,
  ElementRef,
  EventEmitter,
  OnInit,
  Output,
  SkipSelf,
  ViewChild,
} from '@angular/core';
import { SessionApiService } from '../../service/session-api.service';
import { ChatApiService } from '../../service/chat-api.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
})
export class ChatComponent implements OnInit {
  constructor(
    @SkipSelf() private chatService: ChatApiService,
    @SkipSelf() private sessionService: SessionApiService
  ) {}

  @Output() exit = new EventEmitter<void>();
  @ViewChild('inputRef', { static: false }) inputRef!: ElementRef;
  loading: boolean = false;

  ngOnInit(): void {
    this.getMessages('647f3c5170b47d535c175512');
  }

  sendMessage() {
    this.loading = true;
    if (this.inputRef.nativeElement.value != '') {
      this.chatService
        .addChat('647f3c5170b47d535c175512', this.inputRef.nativeElement.value)
        .subscribe((res) => {
          console.log('CCCCCCCCC', this.inputRef.nativeElement.value);

          console.log(res);
          for (let message of res.data.message) {
            if (
              (message.role == 'user' ||
                message.role == 'assistant' ||
                message.role == 'function') &&
              message.content != ''
            )
              this.messageList.push(message);
          }
          this.loading = false;
          this.inputRef.nativeElement.value = '';
        });
    }
  }

  getMessages(sessionId: string) {
    this.loading = true;
    this.sessionService.getSessionById(sessionId).subscribe((res) => {
      for (let message of res.data.messages) {
        if (
          (message.role == 'user' ||
            message.role == 'assistant' ||
            message.role == 'function') &&
          message.content != ''
        )
          this.messageList.push(message);
      }
      this.loading = false;
    });
  }

  messageList: any = [];

  onExit() {
    this.exit.emit();
  }
}
