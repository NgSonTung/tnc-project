import { Component, Input, OnInit, SkipSelf } from '@angular/core';
import { ChatApiService } from '../../service/chat-api.service';

@Component({
  selector: 'app-message',
  templateUrl: './message.component.html',
  styleUrls: ['./message.component.scss'],
})
export class MessageComponent implements OnInit {
  constructor(@SkipSelf() private chatService: ChatApiService) {}

  getImage(imageName: string) {
    this.chatService.getImage(imageName).subscribe((res) => {
      this.imageSrc = res;
    });
  }

  @Input() message: string = '';
  @Input() role: string = 'user';
  @Input() name?: string;
  imageSrc?: string;

  ngOnInit(): void {
    if (this.role == 'function' && this.name == 'draw_bar_graph') {
      //remove .png
      const imageNameWithoutExtension = this.message.slice(0, -4);
      this.getImage(imageNameWithoutExtension);
    }
  }
}
