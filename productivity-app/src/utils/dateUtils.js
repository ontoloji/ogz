import { format, startOfWeek, endOfWeek, startOfMonth, endOfMonth, isWithinInterval } from 'date-fns';
import { tr } from 'date-fns/locale';

export const formatDate = (date, formatStr = 'dd MMMM yyyy') => {
  return format(new Date(date), formatStr, { locale: tr });
};

export const formatTime = (date) => {
  return format(new Date(date), 'HH:mm');
};

export const formatDateTime = (date) => {
  return format(new Date(date), 'dd MMM yyyy HH:mm', { locale: tr });
};

export const getTodayRange = () => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  return { start: today, end: tomorrow };
};

export const getWeekRange = () => {
  const today = new Date();
  return {
    start: startOfWeek(today, { locale: tr }),
    end: endOfWeek(today, { locale: tr })
  };
};

export const getMonthRange = () => {
  const today = new Date();
  return {
    start: startOfMonth(today),
    end: endOfMonth(today)
  };
};

export const isInRange = (date, range) => {
  return isWithinInterval(new Date(date), { start: range.start, end: range.end });
};

export const formatDuration = (minutes) => {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  if (hours === 0) return `${mins}dk`;
  if (mins === 0) return `${hours}sa`;
  return `${hours}sa ${mins}dk`;
};

export const calculateDuration = (start, end) => {
  const diff = new Date(end) - new Date(start);
  return Math.floor(diff / 1000 / 60); // minutes
};

export default {
  formatDate,
  formatTime,
  formatDateTime,
  getTodayRange,
  getWeekRange,
  getMonthRange,
  isInRange,
  formatDuration,
  calculateDuration
};
