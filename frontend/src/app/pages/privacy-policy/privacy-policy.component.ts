import { Component, ChangeDetectionStrategy } from '@angular/core';
import { HeroVideoComponent } from '../../shared/components/hero-video/hero-video.component';

@Component({
  selector: 'app-privacy-policy',
  imports: [HeroVideoComponent],
  templateUrl: './privacy-policy.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrl: './privacy-policy.component.css'
})
export class PrivacyPolicyComponent {

}
