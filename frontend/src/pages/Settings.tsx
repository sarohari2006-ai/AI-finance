import { useAuth } from "../hooks/useAuth";
import { Card, CardHeader, Button, Input } from "../components/ui";
import { useNavigate } from "react-router-dom";

export default function Settings() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-ink-900">Profile / Settings</h1>
        <p className="text-sm text-ink-500 mt-1">Manage your account information.</p>
      </div>

      <Card>
        <CardHeader title="Account" />
        <div className="grid sm:grid-cols-2 gap-4">
          <Input label="Name" value={user?.name || ""} disabled />
          <Input label="Email" value={user?.email || ""} disabled />
          <Input label="Age" value={user?.age?.toString() || "—"} disabled />
          <Input label="Occupation" value={user?.occupation || "—"} disabled />
        </div>
        <p className="text-xs text-ink-500 mt-3">
          Account detail editing is not available in this demo. Financial details can be updated on the Financial Profile page.
        </p>
      </Card>

      <Card>
        <CardHeader title="Session" />
        <Button variant="danger" onClick={handleLogout}>Log out</Button>
      </Card>

      <Card>
        <CardHeader title="Disclaimer" />
        <p className="text-xs text-ink-500">
          This system provides educational and personalized financial guidance based on the information
          provided by the user. It does not constitute professional financial, investment, insurance, tax,
          or legal advice.
        </p>
      </Card>
    </div>
  );
}
