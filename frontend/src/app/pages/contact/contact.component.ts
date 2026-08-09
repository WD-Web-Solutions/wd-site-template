

import { Component, ChangeDetectionStrategy } from '@angular/core';

import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';

import {
  finalize
} from 'rxjs';

import {
  ContactService,
  ContactFormPayload
} from './contact.service';

import { HeroVideoComponent } from '../../shared/components/hero-video/hero-video.component';



@Component({

  selector: 'app-contact',

  standalone: true,

  imports: [
    ReactiveFormsModule,
    HeroVideoComponent
],

  templateUrl:
    './contact.component.html',

  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrl:
    './contact.component.css'

})
export class ContactComponent {


  isSubmitting = false;


  successMessage = '';

  errorMessage = '';



  contactForm;



  services = [

    'Steel Coating & Striping',

    'Seal Coat & Asphalt',

    'Concrete Repairs',

    'Parking Lot Maintenance',

    'Commercial Signage',

    'Wheel Stops & Speed Bumps'

  ];



  constructor(

    private readonly formBuilder: FormBuilder,

    private readonly contactService: ContactService

  ) {


    this.contactForm =
      this.formBuilder.nonNullable.group({


        name: [

          '',

          [

            Validators.required,

            Validators.maxLength(200)

          ]

        ],



        emailAddress: [

          '',

          [

            Validators.required,

            Validators.email,

            Validators.maxLength(254)

          ]

        ],



        company: [

          '',

          [

            Validators.maxLength(200)

          ]

        ],



        phone: [

          '',

          [

            Validators.maxLength(40)

          ]

        ],



        service: [

          '',

          [

            Validators.required

          ]

        ],



        message: [

          '',

          [

            Validators.required,

            Validators.maxLength(4000)

          ]

        ]

      });


  }




  submitContactForm(): void {


    this.successMessage = '';

    this.errorMessage = '';



    if (this.contactForm.invalid) {


      this.contactForm.markAllAsTouched();


      return;

    }



    this.isSubmitting = true;



    const formValue =
      this.contactForm.getRawValue();



    const payload:
      ContactFormPayload = {


        name:
          formValue.name,


        emailAddress:
          formValue.emailAddress,


        company:
          formValue.company || undefined,


        phone:
          formValue.phone || undefined,


        service:
          formValue.service,


        message:
          formValue.message


      };




    this.contactService

      .submitContactForm(payload)

      .pipe(

        finalize(() => {

          this.isSubmitting = false;

        })

      )


      .subscribe({


        next: response => {


          this.successMessage =
            response.message;


          this.contactForm.reset();


        },


        error: () => {


          this.errorMessage =
            'Unable to send request. Please try again.';


        }


      });


  }




  hasError(
    controlName:
      keyof typeof this.contactForm.controls

  ): boolean {


    const control =
      this.contactForm.controls[controlName];



    return (

      control.invalid &&

      (control.touched || control.dirty)

    );


  }


}