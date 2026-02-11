package com.saw.adjustment

import kotlin.math.abs
import kotlin.math.sqrt

/**
 * Pure geometry computation for the saw centering tool.
 * All units are inches in world coordinates with part tip at origin (0,0).
 */
data class SawResult(
    val sawCenterX: Double,
    val sawCenterY: Double,
    val intersectionA: Pair<Double, Double>,
    val intersectionB: Pair<Double, Double>
)

object SawGeometry {

    /**
     * Compute the saw center by intersecting two construction circles.
     *
     * Circle 1: center (-partRadius, rearSlotDepth),  radius = sawRadius
     * Circle 2: center (+partRadius, frontSlotDepth), radius = sawRadius
     *
     * Returns null if no valid intersection exists.
     */
    fun computeSawCenter(
        partDiameter: Double,
        sawDiameter: Double,
        rearSlotDepth: Double,
        frontSlotDepth: Double
    ): SawResult? {
        val partRadius = partDiameter / 2.0
        val sawRadius = sawDiameter / 2.0

        val x1 = -partRadius
        val y1 = rearSlotDepth
        val x2 = partRadius
        val y2 = frontSlotDepth

        val dx = x2 - x1
        val dy = y2 - y1
        val d = sqrt(dx * dx + dy * dy)

        // No intersection if circles are coincident or too far apart
        if (d < 1e-12 || d > 2.0 * sawRadius) return null

        // For equal-radius circles: midpoint offset
        val a = d / 2.0
        val discriminant = sawRadius * sawRadius - a * a
        if (discriminant < 0.0) return null
        val h = sqrt(discriminant)

        val xm = x1 + a * dx / d
        val ym = y1 + a * dy / d

        val ax = xm + h * (-dy) / d
        val ay = ym + h * (dx) / d
        val bx = xm - h * (-dy) / d
        val by = ym - h * (dx) / d

        // Pick the intersection with y < 0 (below the part tip).
        // If both are below, pick the lower one. If neither, pick the lower one anyway.
        val sawX: Double
        val sawY: Double
        if (ay < 0.0 && by >= 0.0) {
            sawX = ax; sawY = ay
        } else if (by < 0.0 && ay >= 0.0) {
            sawX = bx; sawY = by
        } else {
            // Both same sign – pick the lower y
            if (ay <= by) { sawX = ax; sawY = ay } else { sawX = bx; sawY = by }
        }

        return SawResult(
            sawCenterX = sawX,
            sawCenterY = sawY,
            intersectionA = Pair(ax, ay),
            intersectionB = Pair(bx, by)
        )
    }

    fun adjustmentText(h: Double): String {
        return when {
            abs(h) < 1e-6 -> "Saw is centered (no adjustment needed)"
            h > 0 -> "Move saw LEFT by %.4f\"".format(h)
            else -> "Move saw RIGHT by %.4f\"".format(abs(h))
        }
    }
}
