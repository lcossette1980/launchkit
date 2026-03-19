import { get, post } from "./client";
import type { LoginResponse, User } from "../types/api";

export const getMe = () => get<User>("/auth/me");
export const login = (email: string) => post<LoginResponse>("/auth/login", { email });
export const logout = () => post<{ message: string }>("/auth/logout");
