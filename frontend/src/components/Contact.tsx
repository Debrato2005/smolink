import { useState } from 'react';
import { Field } from './ui/Field';
import { Icon } from './ui/Icon';
import { Modal } from './ui/Modal';

export function Contact({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const draft = new URLSearchParams({
    subject: 'Hello from Smolink',
    body: `${message}\n\nFrom: ${name}\nReply to: ${email}`,
  });
  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title="Say hello."
      description="A question, an idea, or just a hello. I would love to hear it."
    >
      <div className="contact-fields">
        <Field
          id="contact-name"
          label="Name"
          autoComplete="name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Your name"
        />
        <Field
          id="contact-email"
          label="Email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@example.com"
        />
        <div className="field">
          <label htmlFor="contact-message">Message</label>
          <textarea
            id="contact-message"
            rows={4}
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="What is on your mind?"
          />
        </div>
        <p className="field-help">
          This opens your email app with a draft. You send it from there.
        </p>
        <a
          className="button-link"
          href={`mailto:debrato2005@gmail.com?${draft.toString().replace(/\+/g, '%20')}`}
        >
          Open email draft <Icon name="mail" />
        </a>
        <a
          className="text-link"
          href="https://x.com/DebratoG"
          target="_blank"
          rel="noopener noreferrer"
        >
          Or find me on X <Icon name="external" size={16} />
        </a>
      </div>
    </Modal>
  );
}
