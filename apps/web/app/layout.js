import "./globals.css";

export const metadata = {
  title: "Lemonfive CRM",
  description: "Pipeline CRM",
};

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
