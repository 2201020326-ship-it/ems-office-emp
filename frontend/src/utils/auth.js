const USER_KEY = "ems_user";

const decodeJwtPayload = (token) => {
  const tokenParts = token.split(".");
  if (tokenParts.length !== 3) {
    throw new Error("Invalid token format");
  }

  const payload = tokenParts[1].replace(/-/g, "+").replace(/_/g, "/");
  const decoded = atob(payload);
  const jsonPayload = decodeURIComponent(
    decoded
      .split("")
      .map((char) => `%${`00${char.charCodeAt(0).toString(16)}`.slice(-2)}`)
      .join(""),
  );

  return JSON.parse(jsonPayload);
};

export const getUserFromToken = (token) => {
  const payload = decodeJwtPayload(token);

  return {
    userId: Number(payload.user_id),
    phone: payload.phone,
    role: payload.role,
  };
};

export const userStorage = {
  set: (user) => localStorage.setItem(USER_KEY, JSON.stringify(user)),
  get: () => {
    const value = localStorage.getItem(USER_KEY);
    return value ? JSON.parse(value) : null;
  },
  clear: () => localStorage.removeItem(USER_KEY),
};
